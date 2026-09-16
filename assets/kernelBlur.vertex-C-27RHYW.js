import{ar as e}from"./QueenComb-B5W5cCCZ.js";import{k as a}from"./kernelBlurVaryingDeclaration-Dp0WWp3x.js";import"./index-Lacmn5nj.js";import"./react-D-uFLJMr.js";import"./motion-mybjp1Q4.js";import"./router-4H5ws2tv.js";import"./queenRepositoryWorld-CyuPyfZ9.js";const t="kernelBlurVertex",o="vertexOutputs.sampleCoord{X}=vertexOutputs.sampleCenter+uniforms.delta*KERNEL_OFFSET{X};";e.IncludesShadersStoreWGSL[t]||(e.IncludesShadersStoreWGSL[t]=o);const i={name:t,shader:o},n="kernelBlurVertexShader",s=`attribute position: vec2f;uniform delta: vec2f;varying sampleCenter: vec2f;
#include<kernelBlurVaryingDeclaration>[0..varyingCount]
#define CUSTOM_VERTEX_DEFINITIONS
@vertex
fn main(input : VertexInputs)->FragmentInputs {const madd: vec2f= vec2f(0.5,0.5);
#define CUSTOM_VERTEX_MAIN_BEGIN
vertexOutputs.sampleCenter=(vertexInputs.position*madd+madd);
#include<kernelBlurVertex>[0..varyingCount]
vertexOutputs.position= vec4f(vertexInputs.position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;e.ShadersStoreWGSL[n]||(e.ShadersStoreWGSL[n]=s);const d=[a,i];for(const r of d)e.IncludesShadersStoreWGSL[r.name]||(e.IncludesShadersStoreWGSL[r.name]=r.shader);const v={name:n,shader:s};export{v as kernelBlurVertexShaderWGSL};
