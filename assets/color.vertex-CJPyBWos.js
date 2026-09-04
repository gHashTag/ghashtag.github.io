import{S as e}from"./QueenCombBabylon-BIAcetCj.js";import{b as r,a as t,c as a,i as d,d as c,e as l,f as s}from"./clipPlaneVertex-Bvp94bum.js";import{f}from"./fogVertexDeclaration-BEcTOuqO.js";import{i as m,f as V,v as x}from"./vertexColorMixing-DPr8D5bV.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-eC2XFed4.js";import"./index-CPCuwncr.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const o="colorVertexShader",n=`attribute vec3 position;
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
}`;e.ShadersStore[o]||(e.ShadersStore[o]=n);const S=[r,t,a,f,m,d,c,l,s,V,x];for(const i of S)e.IncludesShadersStore[i.name]||(e.IncludesShadersStore[i.name]=i.shader);const _={name:o,shader:n};export{_ as colorVertexShader};
