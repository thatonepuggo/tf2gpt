import * as esbuild from "npm:esbuild";
import { denoPlugins } from "jsr:@luca/esbuild-deno-loader";

const quickMkdir = async (dirname) => {
  try {
    await Deno.mkdir(dirname, { recursive: true });
    return dirname;
  } catch (e) {
    if (e instanceof Deno.errors.AlreadyExists) {
      console.log(`dir already exists: ${dirname}`);
      return;
    }
    throw e;
  }
};

const JS_SRC = "./app/assets/js";
const JS_OUT = await quickMkdir("./app/_build/js");

await esbuild.build({
  plugins: [...denoPlugins()],
  entryPoints: [
    `${JS_SRC}/index.ts`,
    `${JS_SRC}/err.ts`,
  ],
  platform: "browser",
  bundle: true,
  minify: true,
  sourcemap: true,
  format: "iife",
  outdir: JS_OUT,
});
await esbuild.stop();
