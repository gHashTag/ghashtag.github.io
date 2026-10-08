import{aJ as e}from"./QueenComb-DNh_PQ6R.js";import{h as n}from"./helperFunctions-D69BreYT.js";import"./index-B8-CxFjX.js";import"./react--6nd5XBq.js";import"./motion-CvAcPNoJ.js";import"./router-CmS70aoX.js";const t="rgbdDecodePixelShader",a=`varying vUV: vec2f;var textureSamplerSampler: sampler;var textureSampler: texture_2d<f32>;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {fragmentOutputs.color=vec4f(fromRGBD(textureSample(textureSampler,textureSamplerSampler,input.vUV)),1.0);}`;e.ShadersStoreWGSL[t]||(e.ShadersStoreWGSL[t]=a);const o=[n];for(const r of o)e.IncludesShadersStoreWGSL[r.name]||(e.IncludesShadersStoreWGSL[r.name]=r.shader);const u={name:t,shader:a};export{u as rgbdDecodePixelShaderWGSL};
