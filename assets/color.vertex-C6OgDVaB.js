import{bS as e}from"./Queen-C_U0yXV5.js";import{b as r,a as t,i as a,c as d,d as c,e as l}from"./bakedVertexAnimation-4lW_jTRp.js";import{c as s,a as f}from"./clipPlaneVertex-Bc933XfT.js";import{f as m}from"./fogVertexDeclaration-BAeY6MT6.js";import{f as V}from"./fogVertex-CvNvY74d.js";import{v as x}from"./vertexColorMixing-DkGo7V3E.js";import"./index-R51P2USl.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const o="colorVertexShader",n=`attribute vec3 position;
#ifdef VERTEXCOLOR
attribute vec4 color;
#endif
#include<bonesDeclaration>
#include<bakedVertexAnimationDeclaration>
#include<clipPlaneVertexDeclaration>
#include<fogVertexDeclaration>
#ifdef FOG
uniform mat4 view;
#endif
#include<instancesDeclaration>
uniform mat4 viewProjection;
#ifdef MULTIVIEW
uniform mat4 viewProjectionR;
#endif
#if defined(VERTEXCOLOR) || defined(INSTANCESCOLOR) && defined(INSTANCES)
varying vec4 vColor;
#endif
#define CUSTOM_VERTEX_DEFINITIONS
void main(void) {
#define CUSTOM_VERTEX_MAIN_BEGIN
#ifdef VERTEXCOLOR
vec4 colorUpdated=color;
#endif
#include<instancesVertex>
#include<bonesVertex>
#include<bakedVertexAnimation>
vec4 worldPos=finalWorld*vec4(position,1.0);
#ifdef MULTIVIEW
if (gl_ViewID_OVR==0u) {gl_Position=viewProjection*worldPos;} else {gl_Position=viewProjectionR*worldPos;}
#else
gl_Position=viewProjection*worldPos;
#endif
#include<clipPlaneVertex>
#include<fogVertex>
#include<vertexColorMixing>
#define CUSTOM_VERTEX_MAIN_END
}`;e.ShadersStore[o]||(e.ShadersStore[o]=n);const S=[r,t,s,m,a,d,c,l,f,V,x];for(const i of S)e.IncludesShadersStore[i.name]||(e.IncludesShadersStore[i.name]=i.shader);const _={name:o,shader:n};export{_ as colorVertexShader};
