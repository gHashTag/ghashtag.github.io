import{ar as e}from"./QueenComb-DojR2dWW.js";import{c as a,a as i}from"./clipPlaneFragment-B3i0Rz8j.js";import{f as d,a as l}from"./fogFragment-DK9uiXF7.js";import"./index-3zHDZIRR.js";import"./react-D-uFLJMr.js";import"./motion-mybjp1Q4.js";import"./router-4H5ws2tv.js";import"./queenRepositoryWorld-CyuPyfZ9.js";const r="colorPixelShader",n=`#if defined(VERTEXCOLOR) || defined(INSTANCESCOLOR) && defined(INSTANCES)
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
}`;e.ShadersStore[r]||(e.ShadersStore[r]=n);const t=[a,d,i,l];for(const o of t)e.IncludesShadersStore[o.name]||(e.IncludesShadersStore[o.name]=o.shader);const E={name:r,shader:n};export{E as colorPixelShader};
