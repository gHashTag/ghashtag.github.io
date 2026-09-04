import{S as e}from"./QueenCombBabylon-BIAcetCj.js";import{k as a}from"./kernelBlurVaryingDeclaration-IYU6gVJi.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-eC2XFed4.js";import"./index-CPCuwncr.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const t="kernelBlurVertex",o="vertexOutputs.sampleCoord{X}=vertexOutputs.sampleCenter+uniforms.delta*KERNEL_OFFSET{X};";e.IncludesShadersStoreWGSL[t]||(e.IncludesShadersStoreWGSL[t]=o);const i={name:t,shader:o},n="kernelBlurVertexShader",s=`attribute position: vec2f;uniform delta: vec2f;varying sampleCenter: vec2f;
#include<kernelBlurVaryingDeclaration>[0..varyingCount]
#define CUSTOM_VERTEX_DEFINITIONS
@vertex
fn main(input : VertexInputs)->FragmentInputs {const madd: vec2f= vec2f(0.5,0.5);
#define CUSTOM_VERTEX_MAIN_BEGIN
vertexOutputs.sampleCenter=(vertexInputs.position*madd+madd);
#include<kernelBlurVertex>[0..varyingCount]
vertexOutputs.position= vec4f(vertexInputs.position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;e.ShadersStoreWGSL[n]||(e.ShadersStoreWGSL[n]=s);const d=[a,i];for(const r of d)e.IncludesShadersStoreWGSL[r.name]||(e.IncludesShadersStoreWGSL[r.name]=r.shader);const x={name:n,shader:s};export{x as kernelBlurVertexShaderWGSL};
