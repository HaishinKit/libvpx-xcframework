# libvpx.xcframework

libvpx **1.17.0**, pinned to upstream commit
`6df3ec34557879fff673706f4a1d9fbd0f3a6f0e`, for HaishinKit and independent use.
Includes software VP8 and VP9 encoding and decoding, ARM NEON optimizations,
static linking, and Release optimization with embedded DWARF debug information.
No external runtime dependencies. AV1 is not included. VP9 uses the default
8-bit configuration; high-bit-depth encoding/decoding is not enabled.

## Platforms

| Platform | Minimum | Architecture |
|---|---|---|
| iOS device | 13.0 | arm64 |
| iOS simulator | 14.0 | arm64 |
| macOS | 11.0 | arm64 |
| Mac Catalyst | 14.0 | arm64 |
| tvOS device | 13.0 | arm64 |
| tvOS simulator | 14.0 | arm64 |
| visionOS device and simulator | 1.0 | arm64 |

Eight XCFramework slices. Intel and watchOS are not included in this initial
configuration. Device/simulator runtime execution and application archive
validation are separate from build/link verification.

## Build

Requires Xcode with all listed SDKs, Python 3, Git and make. No CMake or NASM
is needed for the arm64 configuration.

```sh
./build.sh                         # Fetch, build all slices, create XCFramework and ZIP
./build.sh verify                  # Swift links for all slices; macOS VP8/VP9 round trips
```

Individual operations:

```sh
./build.sh prepare
./build.sh build macos
./build.sh build ios
./build.sh build ios-simulator
./build.sh build maccatalyst
./build.sh build tvos
./build.sh build tvos-simulator
./build.sh build visionos
./build.sh build visionos-simulator
./build.sh package                  # Requires all eight builds
./build.sh local                    # Restore local Swift package manifest
```

Use `JOBS=4` to adjust build concurrency. Each platform build starts clean.
Preparation rejects an unexpected or modified upstream checkout. The upstream
source remains unchanged under `libvpx/`; `build/source/` adds a small SDK-path
override to `build/make/configure.sh` so libvpx's Darwin target can use the
selected Apple SDK. Codec sources are unchanged. Metadata records this adaptation.
After changing source versions or preparation logic, prepare and rebuild all slices.

## Swift Package Manager

After building, add this directory as a local package and use the `libvpx` product:

```swift
import libvpx

let encoder = vpx_codec_vp8_cx() // VP8 encoder interface
let decoder = vpx_codec_vp9_dx() // VP9 decoder interface
```

Public C headers retain their `vpx/` layout and a module map exports `libvpx`.
SwiftPM consumers do not need to add the C++ runtime.

## Distribution

The build creates `libvpx.xcframework`, `libvpx.xcframework.zip`, and
`libvpx.xcframework.zip.sha256`. Nothing is uploaded automatically by the local scripts.

To prepare a release manifest for the intended repository
`https://github.com/HaishinKit/libvpx-xcframework`:

```sh
./build.sh release v1.17.0
swift package dump-package
```

This writes the remote binary URL and computed checksum to the root
`Package.swift` and `dist/Package.swift`. Review and commit the files, tag that
commit, then publish the exact ZIP and checksum on a GitHub Release with the
same tag. The repository and release must exist before remote consumers can
resolve it. Do not rebuild or replace published assets without publishing a new
package version. Restore the development manifest with `./build.sh local`.

## Release from GitHub Actions

After this workflow is on `main`:

1. Open **Actions → Release XCFramework → Run workflow**.
2. Select **main** and enter a package version, such as `1.17.0`.
3. Run the workflow. A successful run publishes `v1.17.0` and its GitHub Release.

The input is the **package distribution version**, not the upstream libvpx
version to download. The source version and commit remain pinned in
`scripts/build.py`. Update those pins in a reviewed change before releasing a
new upstream version. Both `1.17.0` and `v1.17.0` normalize to `v1.17.0`.
Only stable versions are accepted; existing tags and releases (including drafts)
are rejected before building. Release runs are serialized.

The workflow builds all eight slices on an Apple silicon `macos-26` runner with
Xcode 26.6, verifies Swift linking and macOS VP8/VP9 round trips, then generates
the remote Swift package manifest with the exact ZIP checksum. It commits that
manifest and pushes **only the release tag**. `main` retains its local development
manifest; remote SwiftPM consumers select a published version tag.

The built-in `GITHUB_TOKEN` with `contents: write` is sufficient; no personal
access token or signing secret is required. Repository rules must permit the
workflow to create tags and GitHub Releases. The separate **Build XCFramework**
workflow still builds and uploads review artifacts without publishing.

Before pushing the release tag, the release workflow saves the exact ZIP,
checksum, and `dist/Package.swift` as a recovery artifact for 30 days. If
publication fails after the tag is pushed, do **not** rebuild or move the tag:
download the saved artifact, check out the existing tag, restore the ZIP and
checksum to the repository root, and run:

```sh
./build.sh publish v1.17.0
```

Publishing checks the manifest/checksum, clean working tree, matching local and
remote tags at HEAD, and notices inside the ZIP. It refuses to replace an
existing release. If a draft or partial Release already exists, inspect and
complete it using the saved assets instead of overwriting them.

For manual publication, generate the release manifest, commit it, and push the
commit and its tag before running `./build.sh publish TAG`. Local release
preparation never uploads anything. Restore the local manifest with
`./build.sh local` before resuming local development.

Release tooling can be checked without publishing or accessing GitHub:

```sh
python3 tests/verify-release.py
```

## Licenses and app redistribution

libvpx uses BSD 3-Clause, with a separate Google patent grant in `PATENTS`.
`LICENSE`, `PATENTS`, `AUTHORS`, and source provenance are included under the
XCFramework's `Licenses/` directory. Preserve applicable notices in your app's
Open Source Licenses screen or accompanying documentation. SwiftPM does not
automatically copy this top-level directory into the final app.

The BSD license does not require disclosure of your application source.
The patent grant has its own scope and termination conditions; see the original
texts for the exact terms. Check additional notices when changing build inputs.
