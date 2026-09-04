import{S as e}from"./QueenCombBabylon-Ch90MSLm.js";import{h as o}from"./helperFunctions-C_TPpeTi.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-CFJEwTqY.js";import"./index-DHAlv9Zs.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const t="rgbdDecodePixelShader",a=`varying vUV: vec2f;var textureSamplerSampler: sampler;var textureSampler: texture_2d<f32>;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {fragmentOutputs.color=vec4f(fromRGBD(textureSample(textureSampler,textureSamplerSampler,input.vUV)),1.0);}`;e.ShadersStoreWGSL[t]||(e.ShadersStoreWGSL[t]=a);const n=[o];for(const r of n)e.IncludesShadersStoreWGSL[r.name]||(e.IncludesShadersStoreWGSL[r.name]=r.shader);const l={name:t,shader:a};export{l as rgbdDecodePixelShaderWGSL};
