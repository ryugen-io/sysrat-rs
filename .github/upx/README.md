# UPX Compression Flags

This directory contains flag files to enable UPX (Ultimate Packer for eXecutables) compression for binaries.

## How It Works

The presence of specific files in this directory will enable UPX compression during the build process:

### Compression Flags

- `.enable-upx` - Enable UPX compression for **ALL** architectures
- `.enable-upx-x86_64` - Enable UPX compression for x86_64 architectures only
- `.enable-upx-arm` - Enable UPX compression for ARM64/aarch64 architectures only

## Usage Examples

### Enable UPX for all architectures

```bash
touch .github/upx/.enable-upx
git add .github/upx/.enable-upx
git commit -m "build: enable UPX compression for all architectures"
git push
```

### Enable UPX only for x86_64

```bash
touch .github/upx/.enable-upx-x86_64
git add .github/upx/.enable-upx-x86_64
git commit -m "build: enable UPX compression for x86_64 only"
git push
```

### Disable UPX compression

```bash
rm .github/upx/.enable-upx*
git add .github/upx/
git commit -m "build: disable UPX compression"
git push
```

## What is UPX?

UPX is a free, portable, extendable, high-performance executable packer. It compresses executables to reduce their size significantly.

### Advantages

- **Smaller binaries**: Can reduce binary size by 50-70%
- **Faster downloads**: Smaller artifacts mean faster downloads
- **No runtime dependencies**: Decompression happens automatically at runtime

### Disadvantages

- **Slower startup**: Binaries need to decompress at runtime (milliseconds)
- **Antivirus false positives**: Some antivirus software may flag packed binaries
- **Debug limitations**: Packed binaries are harder to debug

## Important Notes

1. UPX compression is **disabled by default**
2. Enable only if you need smaller binary sizes (e.g., for releases)
3. Test thoroughly - UPX can occasionally cause issues with some binaries
4. The CI uses `--best --lzma` for maximum compression

## Recommended Usage

- **Development**: Keep UPX disabled
- **Testing**: Keep UPX disabled
- **Production/Releases**: Enable UPX for specific architectures as needed
