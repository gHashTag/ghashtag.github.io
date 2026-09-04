import{S as e}from"./QueenCombBabylon-C8Ncj2QC.js";import{h as n}from"./helperFunctions-UCED3tzp.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-whyUdQOo.js";import"./index-BtJgdu3X.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const t="rgbdEncodePixelShader",a=`varying vUV: vec2f;var textureSamplerSampler: sampler;var textureSampler: texture_2d<f32>;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {fragmentOutputs.color=toRGBD(textureSample(textureSampler,textureSamplerSampler,input.vUV).rgb);}`;e.ShadersStoreWGSL[t]||(e.ShadersStoreWGSL[t]=a);const o=[n];for(const r of o)e.IncludesShadersStoreWGSL[r.name]||(e.IncludesShadersStoreWGSL[r.name]=r.shader);const c={name:t,shader:a};export{c as rgbdEncodePixelShaderWGSL};
