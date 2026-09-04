import{S as e}from"./QueenCombBabylon-DsB9jNgc.js";import{c as t,a}from"./clipPlaneFragment-CVYdNvIi.js";import{f as i,a as f}from"./fogFragment-CssgAIhZ.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-FX-lN93C.js";import"./index-Xm2cTeAI.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const n="colorPixelShader",o=`#if defined(VERTEXCOLOR) || defined(INSTANCESCOLOR) && defined(INSTANCES)
#define VERTEXCOLOR
varying vColor: vec4f;
#else
uniform color: vec4f;
#endif
#include<clipPlaneFragmentDeclaration>
#include<fogFragmentDeclaration>
#define CUSTOM_FRAGMENT_DEFINITIONS
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {
#define CUSTOM_FRAGMENT_MAIN_BEGIN
#include<clipPlaneFragment>
#if defined(VERTEXCOLOR) || defined(INSTANCESCOLOR) && defined(INSTANCES)
fragmentOutputs.color=input.vColor;
#else
fragmentOutputs.color=uniforms.color;
#endif
#include<fogFragment>(color,fragmentOutputs.color)
#define CUSTOM_FRAGMENT_MAIN_END
}`;e.ShadersStoreWGSL[n]||(e.ShadersStoreWGSL[n]=o);const d=[t,i,a,f];for(const r of d)e.IncludesShadersStoreWGSL[r.name]||(e.IncludesShadersStoreWGSL[r.name]=r.shader);const N={name:n,shader:o};export{N as colorPixelShaderWGSL};
