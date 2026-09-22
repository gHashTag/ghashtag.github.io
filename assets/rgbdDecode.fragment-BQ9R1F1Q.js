import{ar as e}from"./QueenComb-Dp4LGue8.js";import{h as n}from"./helperFunctions-C81dGG_u.js";import"./index-A1kPUqpY.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-CAi4bOxy.js";const t="rgbdDecodePixelShader",a=`varying vUV: vec2f;var textureSamplerSampler: sampler;var textureSampler: texture_2d<f32>;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {fragmentOutputs.color=vec4f(fromRGBD(textureSample(textureSampler,textureSamplerSampler,input.vUV)),1.0);}`;e.ShadersStoreWGSL[t]||(e.ShadersStoreWGSL[t]=a);const o=[n];for(const r of o)e.IncludesShadersStoreWGSL[r.name]||(e.IncludesShadersStoreWGSL[r.name]=r.shader);const u={name:t,shader:a};export{u as rgbdDecodePixelShaderWGSL};
