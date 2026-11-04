# Self-hosted GitHub Actions runner (Docker, Apple Silicon)

This directory contains a Docker Compose setup for running a GitHub
Actions self-hosted runner in a Linux ARM64 container, e.g. on an Apple
Silicon Mac with Docker Desktop.  A containerized runner builds the
`linux-arm64` job natively fast on your own hardware (~1 minute on an
M4 Max instead of ~15-20 minutes on GitHub's hosted ARM runners).

Note that Docker on macOS runs *Linux* containers: this runner can
only execute Linux jobs.  The macOS CI legs continue to use GitHub's
hosted runners.

## Security warning

Self-hosted runners execute arbitrary code from the workflows of the
repository they serve.  On a public repository, pull requests from
anyone can trigger workflow runs on your machine unless restricted.
Before starting the runner:

1. Go to *Settings > Actions > General > Pull requests from forked
   repositories* and require approval for workflow runs from outside
   collaborators ("Require approval for first-time contributors" at
   minimum; "Require approval for all outside collaborators" is
   safer).
2. Alternatively keep this runner for manual `workflow_dispatch` runs
   only (see the workflow in `.github/workflows/build-selfhosted.yml`)
   and stop the container when not needed.

## Setup

1. Create a classic personal access token with the `repo` scope:
   https://github.com/settings/tokens

2. Copy the environment file and fill in the token:

   ```sh
   cd contrib/ci/self-hosted-runner
   cp .env.example .env
   # edit .env, set ACCESS_TOKEN
   ```

3. Start the runner:

   ```sh
   docker compose up -d
   docker compose logs -f       # watch it register
   ```

   The runner appears under *Settings > Actions > Runners* on the
   repository.

4. In Docker Desktop, give the VM enough resources (e.g. 12-16 CPUs,
   24 GB RAM) under *Settings > Resources*.

## Automatic self-hosted with hosted fallback

The main build workflow prefers your self-hosted runners when they
are online and falls back to GitHub's hosted runners when they are
not (for example when the Mac is asleep).  This requires the
repository secret `RUNNER_ADMIN_TOKEN`:

1. Create a classic personal access token with the `repo` scope
   (the same token used for the Docker runner works).
2. Add it under *Settings > Secrets and variables > Actions > New
   repository secret* as `RUNNER_ADMIN_TOKEN`.

Without the secret the build always uses GitHub's hosted runners.
Pull requests from forks never receive repository secrets, so they
always use the hosted runners as well.

## Usage

The workflow `.github/workflows/build-selfhosted.yml` builds the
project explicitly on this runner.  It is triggered manually
(*Actions > Build (self-hosted) > Run workflow*) so that pull request
checks on GitHub's hosted runners are never blocked while the Mac is
asleep.  Start it whenever you want a fast native build:

```sh
gh workflow run build-selfhosted.yml --repo fred-corp/qucsator \
    --ref <branch>
```

The built `qucsator` binary is uploaded as a run artifact; being a
Linux ARM64 binary it is not a drop-in replacement for Qucs-S on
macOS, but it is a fast correctness check of the full build and test
suite on your hardware.

## macOS jobs on your hardware instead

macOS jobs cannot run inside Docker (Linux containers only), so the
macOS leg uses a *native* runner installed directly on the Mac:

1. On the repository go to *Settings > Actions > Runners > New
   self-hosted runner*, select **macOS / ARM64**.  GitHub shows a
   registration token.

2. On the Mac:

   ```sh
   mkdir -p ~/actions-runner && cd ~/actions-runner
   curl -o actions.tar.gz -L https://github.com/actions/runner/releases/download/v2.327.1/actions-runner-osx-arm64-2.327.1.tar.gz
   tar xzf actions.tar.gz
   ./config.sh --url https://github.com/fred-corp/qucsator --token <TOKEN> \
       --labels self-hosted,macOS,arm64 --name m4max-macos
   ```
   (use the runner version and token GitHub shows you; never commit
   the token anywhere)

3. Install it as a launchd service so it survives reboots:

   ```sh
   ./svc.sh install
   ./svc.sh start
   ```

   The service runs as your user; builds execute in your home
   directory context.  Since this runner is not containerized,
   workflow code runs directly on your Mac: keep the forked-PR
   approval requirement described above, and consider stopping the
   service (`./svc.sh stop`) when you do not need it.

The `macos` job in `.github/workflows/build-selfhosted.yml` runs on
this runner and uploads a native macOS ARM64 `qucsator` binary, which
*is* a drop-in replacement for `qucsator_rf` in the Qucs-S
application bundle.
