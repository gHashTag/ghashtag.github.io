import{S as e}from"./QueenCombBabylon-cBwhf22i.js";import{b as t,a as o,c as a,i as c,d,e as s,f as l,g as f,h as S,v as x}from"./vertexColorMixing-Dr_cv9Qj.js";import{f as m}from"./fogVertexDeclaration-FbB9Mx-X.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-CRQhWGsa.js";import"./index-DLCfuEAH.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const n="colorVertexShader",r=`attribute position: vec3f;
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
}`;e.ShadersStoreWGSL[n]||(e.ShadersStoreWGSL[n]=r);const u=[t,o,a,m,c,d,s,l,f,S,x];for(const i of u)e.IncludesShadersStoreWGSL[i.name]||(e.IncludesShadersStoreWGSL[i.name]=i.shader);const C={name:n,shader:r};export{C as colorVertexShaderWGSL};
