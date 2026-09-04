import{S as r}from"./QueenCombBabylon-DsB9jNgc.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-FX-lN93C.js";import"./index-Xm2cTeAI.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const e="depthBoxBlurPixelShader",t=`varying vUV: vec2f;var textureSamplerSampler: sampler;var textureSampler: texture_2d<f32>;uniform screenSize: vec2f;
#define CUSTOM_FRAGMENT_DEFINITIONS
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {var colorDepth: vec4f=vec4f(0.0);for (var x: i32=-OFFSET; x<=OFFSET; x++) {for (var y: i32=-OFFSET; y<=OFFSET; y++) {colorDepth+=textureSample(textureSampler,textureSamplerSampler,input.vUV+ vec2f(f32(x),f32(y))/uniforms.screenSize);}}
fragmentOutputs.color=(colorDepth/ f32((OFFSET*2+1)*(OFFSET*2+1)));}`;r.ShadersStoreWGSL[e]||(r.ShadersStoreWGSL[e]=t);const n={name:e,shader:t};export{n as depthBoxBlurPixelShaderWGSL};
