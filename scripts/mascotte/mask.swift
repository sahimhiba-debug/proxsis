import Foundation
import Vision
import CoreImage
import AppKit

let args = CommandLine.arguments
let input = URL(fileURLWithPath: args[1])
let outDir = URL(fileURLWithPath: args[2])
guard let ciImage = CIImage(contentsOf: input) else { fatalError("no image") }
let handler = VNImageRequestHandler(ciImage: ciImage)
let req = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([req])
guard let result = req.results?.first else { fatalError("no result") }
print("instances:", result.allInstances.count)
let ctx = CIContext()
func save(_ buf: CVPixelBuffer, _ name: String) {
    let ci = CIImage(cvPixelBuffer: buf)
    let cs = CGColorSpaceCreateDeviceGray()
    let url = outDir.appendingPathComponent(name)
    try! ctx.writePNGRepresentation(of: ci, to: url, format: .L8, colorSpace: cs)
}
let all = try result.generateScaledMaskForImage(forInstances: result.allInstances, from: handler)
save(all, "mask_all.png")
for i in result.allInstances {
    let m = try result.generateScaledMaskForImage(forInstances: IndexSet(integer: i), from: handler)
    save(m, "mask_\(i).png")
}
