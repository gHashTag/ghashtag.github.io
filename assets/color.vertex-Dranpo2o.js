import{S as e}from"./QueenCombBabylon-DOdGX8_Q.js";import{b as n,a as t,i as a,c as d,d as c}from"./bakedVertexAnimation-Cp95330r.js";import{c as l,a as s}from"./clipPlaneVertex-Dev4vbRp.js";import{f}from"./fogVertexDeclaration-B2CGHD25.js";import{i as m}from"./instancesDeclaration-DH2uFREj.js";import{f as V}from"./fogVertex-FCqoLcVz.js";import{v as x}from"./vertexColorMixing-BWJ2yWuU.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-DB_P-JXd.js";import"./index--wm36luZ.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const o="colorVertexShader",r=`attribute vec3 position;
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
}`;e.ShadersStore[o]||(e.ShadersStore[o]=r);const p=[n,t,l,f,m,a,d,c,s,V,x];for(const i of p)e.IncludesShadersStore[i.name]||(e.IncludesShadersStore[i.name]=i.shader);const g={name:o,shader:r};export{g as colorVertexShader};
