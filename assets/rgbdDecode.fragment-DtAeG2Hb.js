import{ar as e}from"./ray-nqp9MIGV.js";import{h as o}from"./helperFunctions-BaJSKuPC.js";import"./react-BikoVsHo.js";import"./QueenUniverse-ySrqazwA.js";import"./index-BZfTeQdo.js";import"./motion-DmZWFm6O.js";import"./router-CAi4bOxy.js";import"./specCatalog-ONQ2RJG4.js";const t="rgbdDecodePixelShader",a=`varying vUV: vec2f;var textureSamplerSampler: sampler;var textureSampler: texture_2d<f32>;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {fragmentOutputs.color=vec4f(fromRGBD(textureSample(textureSampler,textureSamplerSampler,input.vUV)),1.0);}`;e.ShadersStoreWGSL[t]||(e.ShadersStoreWGSL[t]=a);const n=[o];for(const r of n)e.IncludesShadersStoreWGSL[r.name]||(e.IncludesShadersStoreWGSL[r.name]=r.shader);const l={name:t,shader:a};export{l as rgbdDecodePixelShaderWGSL};
