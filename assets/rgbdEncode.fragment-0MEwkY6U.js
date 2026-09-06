import{bY as e}from"./Queen-nAuG3tsK.js";import{h as n}from"./helperFunctions-kO3JqXHN.js";import"./index-Yb5zHw8F.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const t="rgbdEncodePixelShader",a=`varying vUV: vec2f;var textureSamplerSampler: sampler;var textureSampler: texture_2d<f32>;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {fragmentOutputs.color=toRGBD(textureSample(textureSampler,textureSamplerSampler,input.vUV).rgb);}`;e.ShadersStoreWGSL[t]||(e.ShadersStoreWGSL[t]=a);const o=[n];for(const r of o)e.IncludesShadersStoreWGSL[r.name]||(e.IncludesShadersStoreWGSL[r.name]=r.shader);const u={name:t,shader:a};export{u as rgbdEncodePixelShaderWGSL};
