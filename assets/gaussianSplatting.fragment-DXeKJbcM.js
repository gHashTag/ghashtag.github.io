import{bG as a}from"./Queen-BlMhzctN.js";import{c as t,a as l}from"./clipPlaneFragment-DADMcwMI.js";import{l as c}from"./logDepthDeclaration-w7NLUIs4.js";import{f as g,a as s}from"./fogFragment-Bn3Pioyz.js";import{p as d}from"./packingFunctions-Yri55npk.js";import{l as f}from"./logDepthFragment-B2jfmHwN.js";import"./index-H5-AQrmI.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const o="gaussianSplattingFragmentDeclaration",i=`vec4 gaussianColor(vec4 inColor)
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
`;a.ShadersStore[n]||(a.ShadersStore[n]=r);const p=[t,c,g,d,f,s,m,l];for(const e of p)a.IncludesShadersStore[e.name]||(a.IncludesShadersStore[e.name]=e.shader);const I={name:n,shader:r};export{I as gaussianSplattingPixelShader};
