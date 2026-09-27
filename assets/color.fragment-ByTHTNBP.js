import{ar as e}from"./QueenComb-Duy8Q2Xw.js";import{c as a,a as i}from"./clipPlaneFragment-BcYKHnfT.js";import{f as d,a as l}from"./fogFragment-BBMn2q1P.js";import"./index-DdRdJilr.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-CAi4bOxy.js";const r="colorPixelShader",n=`#if defined(VERTEXCOLOR) || defined(INSTANCESCOLOR) && defined(INSTANCES)
#define VERTEXCOLOR
varying vec4 vColor;
#else
uniform vec4 color;
#endif
#include<clipPlaneFragmentDeclaration>
#include<fogFragmentDeclaration>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) {
#define CUSTOM_FRAGMENT_MAIN_BEGIN
#include<clipPlaneFragment>
#if defined(VERTEXCOLOR) || defined(INSTANCESCOLOR) && defined(INSTANCES)
gl_FragColor=vColor;
#else
gl_FragColor=color;
#endif
#include<fogFragment>(color,gl_FragColor)
#define CUSTOM_FRAGMENT_MAIN_END
}`;e.ShadersStore[r]||(e.ShadersStore[r]=n);const t=[a,d,i,l];for(const o of t)e.IncludesShadersStore[o.name]||(e.IncludesShadersStore[o.name]=o.shader);const N={name:r,shader:n};export{N as colorPixelShader};
