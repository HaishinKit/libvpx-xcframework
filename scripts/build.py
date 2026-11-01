#!/usr/bin/env python3
"""Build pinned libvpx with Apple clang; no third-party runtime dependencies."""
import json, os, pathlib, shutil, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
os.chdir(ROOT)
VERSION = '1.17.0'
COMMIT = '6df3ec34557879fff673706f4a1d9fbd0f3a6f0e'
URL = 'https://chromium.googlesource.com/webm/libvpx'
# name: SDK, clang target. Simulator deployment targets follow the sibling packages.
PLATFORMS = {
 'ios': ('iphoneos', 'arm64-apple-ios13.0'),
 'ios-simulator': ('iphonesimulator', 'arm64-apple-ios14.0-simulator'),
 'macos': ('macosx', 'arm64-apple-macos11.0'),
 'maccatalyst': ('macosx', 'arm64-apple-ios14.0-macabi'),
 'tvos': ('appletvos', 'arm64-apple-tvos13.0'),
 'tvos-simulator': ('appletvsimulator', 'arm64-apple-tvos14.0-simulator'),
 'visionos': ('xros', 'arm64-apple-xros1.0'),
 'visionos-simulator': ('xrsimulator', 'arm64-apple-xros1.0-simulator'),
}
def run(*args, **kwargs):
 return subprocess.check_output(args, text=True, **kwargs).strip()
def prepare():
 src = ROOT / 'libvpx'
 if not src.exists():
  subprocess.run(['git','clone','--depth','1','--branch',f'v{VERSION}',URL,str(src)],check=True)
 if run('git','-C',str(src),'rev-parse','HEAD') != COMMIT:
  raise SystemExit('Unexpected libvpx revision')
 if run('git','-C',str(src),'status','--porcelain'):
  raise SystemExit('Upstream checkout must be clean')
 # Keep upstream unmodified. Apply the SDK-selection adaptation to a build copy.
 target = ROOT / 'build/source'
 if target.exists(): shutil.rmtree(target)
 shutil.copytree(src,target,ignore=shutil.ignore_patterns('.git'))
 config = target / 'build/make/configure.sh'
 text = config.read_text()
 needle = 'show_darwin_sdk_path() {\n'
 assert text.count(needle) == 1
 config.write_text(text.replace(needle, needle + '  if [ -n "${LIBVPX_APPLE_SYSROOT:-}" ]; then\n    printf "%s\\n" "$LIBVPX_APPLE_SYSROOT"\n    return\n  fi\n'))
 (ROOT/'build/source.json').write_text(json.dumps({'version':VERSION,'commit':COMMIT,'url':URL,'adaptation':'SDK path override in configure.sh; codec sources unchanged'},indent=2)+'\n')
def build(name):
 sdk, triple = PLATFORMS[name]
 if not (ROOT/'build/source/configure').exists(): raise SystemExit('Run ./build.sh prepare first')
 directory = ROOT/'build'/name
 # Never reuse configuration from another toolchain.
 if directory.exists(): shutil.rmtree(directory)
 directory.mkdir(parents=True)
 sysroot = run('xcrun','--sdk',sdk,'--show-sdk-path')
 clang = run('xcrun','--sdk',sdk,'--find','clang')
 flags = f'-target {triple} -isysroot {sysroot}'
 env = dict(os.environ, LIBVPX_APPLE_SYSROOT=sysroot, CC=clang, CXX=run('xcrun','--sdk',sdk,'--find','clang++'), AR=run('xcrun','--find','ar'), AS=clang+' -c', LD=clang,
            CFLAGS=flags, CXXFLAGS=flags, ASFLAGS=flags, LDFLAGS=flags)
 prefix = directory/'install'
 subprocess.run([str(ROOT/'build/source/configure'),'--target=arm64-darwin25-gcc',f'--prefix={prefix}',
  '--enable-vp8','--enable-vp9','--enable-pic','--enable-debug','--disable-shared','--enable-static',
  '--disable-examples','--disable-tools','--disable-docs','--disable-unit-tests','--disable-install-srcs'],cwd=directory,env=env,check=True)
 subprocess.run(['make','-j'+os.environ.get('JOBS','8')],cwd=directory,env=env,check=True)
 subprocess.run(['make','install'],cwd=directory,env=env,check=True)
 (directory/'source.json').write_bytes((ROOT/'build/source.json').read_bytes())
 headers = prefix/'include'
 (headers/'module.modulemap').write_text('module libvpx [system] {\n  umbrella "vpx"\n  export *\n}\n')
def package():
 args = ['xcodebuild','-create-xcframework']
 for name in PLATFORMS:
  directory = ROOT/'build'/name
  if (directory/'source.json').read_bytes() != (ROOT/'build/source.json').read_bytes():
   raise SystemExit(f'Stale build: {name}')
  args += ['-library',str(directory/'install/lib/libvpx.a'),'-headers',str(directory/'install/include')]
 output = ROOT/'libvpx.xcframework'
 if output.exists(): shutil.rmtree(output)
 subprocess.run(args+['-output',str(output)],check=True)
 licenses = output/'Licenses'
 licenses.mkdir()
 for name in ['LICENSE','PATENTS','AUTHORS']:
  shutil.copy2(ROOT/'libvpx'/name,licenses/name)
 shutil.copy2(ROOT/'build/source.json',licenses/'SOURCES.json')
 archive = ROOT/'libvpx.xcframework.zip'
 archive.unlink(missing_ok=True)
 subprocess.run(['/usr/bin/zip','-qry',str(archive),output.name],check=True,env=dict(os.environ,COPYFILE_DISABLE='1'))
 checksum = run('swift','package','compute-checksum',str(archive))
 (ROOT/'libvpx.xcframework.zip.sha256').write_text(checksum+'\n')
def release(tag):
 subprocess.run([sys.executable,str(ROOT/'scripts/release-manifest.py'),'release',tag],check=True)
command = sys.argv[1] if len(sys.argv)>1 else 'all'
if command == 'prepare': prepare()
elif command == 'build':
 for name in ([sys.argv[2]] if len(sys.argv)>2 else PLATFORMS): build(name)
elif command == 'package': package()
elif command == 'verify':
 subprocess.run([sys.executable,str(ROOT/'scripts/release-manifest.py'),'check-local'],check=True)
 subprocess.run([sys.executable,str(ROOT/'tests/verify.py')],check=True)
elif command == 'local': subprocess.run([sys.executable,str(ROOT/'scripts/release-manifest.py'),'local'],check=True)
elif command == 'release': release(sys.argv[2])
elif command == 'publish': subprocess.run([sys.executable,str(ROOT/'scripts/publish.py'),sys.argv[2]],check=True)
elif command == 'all':
 prepare()
 for name in PLATFORMS: build(name)
 package()
 shutil.copy2(ROOT/'support/Package.swift', ROOT/'Package.swift')
else: raise SystemExit('Commands: all, prepare, build [platform], package, local, release TAG, publish TAG')
