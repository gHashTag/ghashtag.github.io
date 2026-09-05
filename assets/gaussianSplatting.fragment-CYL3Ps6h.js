import{bM as n}from"./Queen-BwxyLMhx.js";import{c as o,a as s}from"./clipPlaneFragment-DfAgVW1m.js";import{l}from"./logDepthDeclaration-Dq3rE4wd.js";import{f,a as c}from"./fogFragment-dX2zlauN.js";import{p as g}from"./packingFunctions-IeEKgl1-.js";import{l as m}from"./logDepthFragment-Dkf5IGo8.js";import"./index-C_EEfoWV.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const a="gaussianSplattingFragmentDeclaration",i=`fn gaussianColor(inColor: vec4f,inPosition: vec2f)->vec4f
{var A : f32=-dot(inPosition,inPosition);if (A>-4.0)
{var B: f32=exp(A)*inColor.a;
#include<logDepthFragment>
var color: vec3f=inColor.rgb;
#ifdef FOG
#include<fogFragment>
#endif
return vec4f(color,B);} else {return vec4f(0.0);}}
`;n.IncludesShadersStoreWGSL[a]||(n.IncludesShadersStoreWGSL[a]=i);const p={name:a,shader:i},t="gaussianSplattingPixelShader",r=`#include<clipPlaneFragmentDeclaration>
#include<logDepthDeclaration>
#include<fogFragmentDeclaration>
#ifdef GPUPICKER_PACK_DEPTH
#include<packingFunctions>
#endif
varying vColor: vec4f;varying vPosition: vec2f;
#define CUSTOM_FRAGMENT_DEFINITIONS
#include<gaussianSplattingFragmentDeclaration>
@fragment
fn main(input: FragmentInputs)->FragmentOutputs {
#define CUSTOM_FRAGMENT_MAIN_BEGIN
#include<clipPlaneFragment>
var finalColor: vec4f=gaussianColor(input.vColor,input.vPosition);
#define CUSTOM_FRAGMENT_BEFORE_FRAGCOLOR
#ifdef GPUPICKER_DEPTH
fragmentOutputs.fragData0=finalColor;
#ifdef GPUPICKER_PACK_DEPTH
fragmentOutputs.fragData1=pack(fragmentInputs.position.z);
#else
fragmentOutputs.fragData1=vec4f(fragmentInputs.position.z,0.0,0.0,1.0);
#endif
#else
fragmentOutputs.color=finalColor;
#endif
#define CUSTOM_FRAGMENT_MAIN_END
}
`;n.ShadersStoreWGSL[t]||(n.ShadersStoreWGSL[t]=r);const S=[o,l,f,g,m,c,p,s];for(const e of S)n.IncludesShadersStoreWGSL[e.name]||(n.IncludesShadersStoreWGSL[e.name]=e.shader);const L={name:t,shader:r};export{L as gaussianSplattingPixelShaderWGSL};
