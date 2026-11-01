// swift-tools-version: 5.9
import PackageDescription
let package = Package(
    name: "libvpx",
    platforms: [.iOS(.v13), .tvOS(.v13), .macOS(.v11), .macCatalyst(.v14), .visionOS(.v1)],
    products: [.library(name: "libvpx", targets: ["libvpx"])],
    targets: [.binaryTarget(name: "libvpx", url: "https://github.com/HaishinKit/libvpx-xcframework/releases/download/v1.17.0/libvpx.xcframework.zip", checksum: "231e4e6dfaaec894f99e454b776e187da9e6aa4857629a6fb5370fae4ce0f429")]
)
