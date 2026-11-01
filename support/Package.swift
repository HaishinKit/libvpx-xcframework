// swift-tools-version: 5.9
import PackageDescription
let package = Package(
    name: "libvpx",
    platforms: [.iOS(.v13), .tvOS(.v13), .macOS(.v11), .macCatalyst(.v14), .visionOS(.v1)],
    products: [.library(name: "libvpx", targets: ["libvpx"])],
    targets: [.binaryTarget(name: "libvpx", path: "libvpx.xcframework")]
)
