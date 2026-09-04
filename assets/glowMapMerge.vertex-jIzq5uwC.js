import{bF as t}from"./Queen-Dsc8P5sb.js";import"./index-0PdQE9FR.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const e="glowMapMergeVertexShader",r=`attribute position: vec2f;varying vUV: vec2f;
#define CUSTOM_VERTEX_DEFINITIONS
@vertex
fn main(input : VertexInputs)->FragmentInputs {const madd: vec2f= vec2f(0.5,0.5);
#define CUSTOM_VERTEX_MAIN_BEGIN
vertexOutputs.vUV=vertexInputs.position*madd+madd;vertexOutputs.position= vec4f(vertexInputs.position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}`;t.ShadersStoreWGSL[e]||(t.ShadersStoreWGSL[e]=r);const a={name:e,shader:r};export{a as glowMapMergeVertexShaderWGSL};
