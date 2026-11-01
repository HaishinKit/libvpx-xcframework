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

The included manual GitHub Actions workflow builds and verifies the package,
and uploads build artifacts for review. It does not create tags or publish releases.

## Licenses and app redistribution

libvpx uses BSD 3-Clause, with a separate Google patent grant in `PATENTS`.
`LICENSE`, `PATENTS`, `AUTHORS`, and source provenance are included under the
XCFramework's `Licenses/` directory. Preserve applicable notices in your app's
Open Source Licenses screen or accompanying documentation. SwiftPM does not
automatically copy this top-level directory into the final app.

The BSD license does not require disclosure of your application source.
The patent grant has its own scope and termination conditions; see the original
texts for the exact terms. Check additional notices when changing build inputs.
