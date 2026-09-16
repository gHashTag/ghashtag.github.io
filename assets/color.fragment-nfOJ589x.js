import{ar as e}from"./QueenComb-B5W5cCCZ.js";import{c as a,a as t}from"./clipPlaneFragment-B70F8VAF.js";import{f as i,a as f}from"./fogFragment-D7ZWowhC.js";import"./index-Lacmn5nj.js";import"./react-D-uFLJMr.js";import"./motion-mybjp1Q4.js";import"./router-4H5ws2tv.js";import"./queenRepositoryWorld-CyuPyfZ9.js";const n="colorPixelShader",o=`#if defined(VERTEXCOLOR) || defined(INSTANCESCOLOR) && defined(INSTANCES)
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
}`;e.ShadersStoreWGSL[n]||(e.ShadersStoreWGSL[n]=o);const d=[a,i,t,f];for(const r of d)e.IncludesShadersStoreWGSL[r.name]||(e.IncludesShadersStoreWGSL[r.name]=r.shader);const O={name:n,shader:o};export{O as colorPixelShaderWGSL};
