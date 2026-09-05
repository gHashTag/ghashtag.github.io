import{bG as e}from"./Queen-mC2OQEDY.js";import{b as o,a as t,i as a,c,d}from"./bakedVertexAnimation-BXX_TEWl.js";import{c as s,a as f}from"./clipPlaneVertex-Bhm_9Js9.js";import{f as l}from"./fogVertexDeclaration-Dh1SQO5b.js";import{i as S}from"./instancesDeclaration-DQPS5W_6.js";import{f as m}from"./fogVertex-Cr59tzTE.js";import{v as x}from"./vertexColorMixing-BCS0tHGQ.js";import"./index-BDsYAmx2.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const r="colorVertexShader",n=`attribute position: vec3f;
#ifdef VERTEXCOLOR
attribute color: vec4f;
#endif
#include<bonesDeclaration>
#include<bakedVertexAnimationDeclaration>
#include<clipPlaneVertexDeclaration>
#include<fogVertexDeclaration>
#ifdef FOG
uniform view: mat4x4f;
#endif
#include<instancesDeclaration>
uniform viewProjection: mat4x4f;
#if defined(VERTEXCOLOR) || defined(INSTANCESCOLOR) && defined(INSTANCES)
varying vColor: vec4f;
#endif
#define CUSTOM_VERTEX_DEFINITIONS
@vertex
fn main(input : VertexInputs)->FragmentInputs {
#define CUSTOM_VERTEX_MAIN_BEGIN
#ifdef VERTEXCOLOR
var colorUpdated: vec4f=vertexInputs.color;
#endif
#include<instancesVertex>
#include<bonesVertex>
#include<bakedVertexAnimation>
var worldPos: vec4f=finalWorld* vec4f(vertexInputs.position,1.0);vertexOutputs.position=uniforms.viewProjection*worldPos;
#include<clipPlaneVertex>
#include<fogVertex>
#include<vertexColorMixing>
#define CUSTOM_VERTEX_MAIN_END
}`;e.ShadersStoreWGSL[r]||(e.ShadersStoreWGSL[r]=n);const p=[o,t,s,l,S,a,c,d,f,m,x];for(const i of p)e.IncludesShadersStoreWGSL[i.name]||(e.IncludesShadersStoreWGSL[i.name]=i.shader);const D={name:r,shader:n};export{D as colorVertexShaderWGSL};
