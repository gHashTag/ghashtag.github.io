import{ar as e}from"./ray-nqp9MIGV.js";import{c as i,a}from"./clipPlaneFragment-qFiNm83g.js";import{f as d,a as l}from"./fogFragment-NxLGFnku.js";import"./react-BikoVsHo.js";import"./QueenUniverse-ySrqazwA.js";import"./index-BZfTeQdo.js";import"./motion-DmZWFm6O.js";import"./router-CAi4bOxy.js";import"./specCatalog-ONQ2RJG4.js";const r="colorPixelShader",n=`#if defined(VERTEXCOLOR) || defined(INSTANCESCOLOR) && defined(INSTANCES)
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
}`;e.ShadersStore[r]||(e.ShadersStore[r]=n);const t=[i,d,a,l];for(const o of t)e.IncludesShadersStore[o.name]||(e.IncludesShadersStore[o.name]=o.shader);const F={name:r,shader:n};export{F as colorPixelShader};
