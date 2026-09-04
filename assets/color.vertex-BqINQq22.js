import{S as e}from"./QueenCombBabylon-Ch90MSLm.js";import{b as t,a as o,c as a,i as c,d,e as s,f}from"./clipPlaneVertex-CEe6kMDs.js";import{f as l}from"./fogVertexDeclaration-PqJngMQ5.js";import{i as S,f as x,v as m}from"./vertexColorMixing-9yNb81Fz.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-CFJEwTqY.js";import"./index-DHAlv9Zs.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const n="colorVertexShader",r=`attribute position: vec3f;
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
}`;e.ShadersStoreWGSL[n]||(e.ShadersStoreWGSL[n]=r);const u=[t,o,a,l,S,c,d,s,f,x,m];for(const i of u)e.IncludesShadersStoreWGSL[i.name]||(e.IncludesShadersStoreWGSL[i.name]=i.shader);const D={name:n,shader:r};export{D as colorVertexShaderWGSL};
