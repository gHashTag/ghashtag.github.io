import{S as a}from"./QueenCombBabylon-DJ7kDGWi.js";import{c as t,a as l}from"./clipPlaneFragment-BNY9_yI-.js";import{l as c}from"./logDepthDeclaration-DuFzBxDR.js";import{f as g,a as s}from"./fogFragment-DUHOei-8.js";import{p as d}from"./packingFunctions-CIobfnK6.js";import{l as f}from"./logDepthFragment--jVSWmIj.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-DOtFzvQe.js";import"./index-Za6t80dQ.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const o="gaussianSplattingFragmentDeclaration",i=`vec4 gaussianColor(vec4 inColor)
{float A=-dot(vPosition,vPosition);if (A<-4.0) discard;float B=exp(A)*inColor.a;
#include<logDepthFragment>
vec3 color=inColor.rgb;
#ifdef FOG
#include<fogFragment>
#endif
return vec4(color,B);}
`;a.IncludesShadersStore[o]||(a.IncludesShadersStore[o]=i);const m={name:o,shader:i},n="gaussianSplattingPixelShader",r=`#include<clipPlaneFragmentDeclaration>
#include<logDepthDeclaration>
#include<fogFragmentDeclaration>
#ifdef GPUPICKER_DEPTH
layout(location=0) out highp vec4 glFragData[2];
#endif
#ifdef GPUPICKER_PACK_DEPTH
#include<packingFunctions>
#endif
varying vec4 vColor;varying vec2 vPosition;
#define CUSTOM_FRAGMENT_DEFINITIONS
#include<gaussianSplattingFragmentDeclaration>
void main () {
#define CUSTOM_FRAGMENT_MAIN_BEGIN
#include<clipPlaneFragment>
vec4 finalColor=gaussianColor(vColor);
#define CUSTOM_FRAGMENT_BEFORE_FRAGCOLOR
#ifdef GPUPICKER_DEPTH
glFragData[0]=finalColor;
#ifdef GPUPICKER_PACK_DEPTH
glFragData[1]=pack(gl_FragCoord.z);
#else
glFragData[1]=vec4(gl_FragCoord.z,0.0,0.0,1.0);
#endif
#else
gl_FragColor=finalColor;
#endif
#define CUSTOM_FRAGMENT_MAIN_END
}
`;a.ShadersStore[n]||(a.ShadersStore[n]=r);const p=[t,c,g,d,f,s,m,l];for(const e of p)a.IncludesShadersStore[e.name]||(a.IncludesShadersStore[e.name]=e.shader);const A={name:n,shader:r};export{A as gaussianSplattingPixelShader};
