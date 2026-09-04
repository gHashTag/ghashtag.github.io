import{S as t}from"./QueenCombBabylon-cBwhf22i.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-CRQhWGsa.js";import"./index-DLCfuEAH.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const e="postprocessVertexShader",r=`attribute position: vec2<f32>;uniform scale: vec2<f32>;varying vUV: vec2<f32>;const madd=vec2(0.5,0.5);
#define CUSTOM_VERTEX_DEFINITIONS
@vertex
fn main(input : VertexInputs)->FragmentInputs {
#define CUSTOM_VERTEX_MAIN_BEGIN
vertexOutputs.vUV=(vertexInputs.position*madd+madd)*uniforms.scale;vertexOutputs.position=vec4(vertexInputs.position,0.0,1.0);
#define CUSTOM_VERTEX_MAIN_END
}
`;t.ShadersStoreWGSL[e]||(t.ShadersStoreWGSL[e]=r);const S={name:e,shader:r};export{S as postprocessVertexShaderWGSL};
