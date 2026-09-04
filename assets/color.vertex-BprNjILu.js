import{S as e}from"./QueenCombBabylon-Ccpv0aSp.js";import{b as t,a as n,i as a,c,d}from"./bakedVertexAnimation-VHXhNDN8.js";import{c as s,a as f}from"./clipPlaneVertex-C_e4t6Gc.js";import{f as l}from"./fogVertexDeclaration-Lj-LoECG.js";import{i as S}from"./instancesDeclaration-DAsZKqSY.js";import{f as m}from"./fogVertex-D8pwMge5.js";import{v as x}from"./vertexColorMixing-BM0Ggvi6.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-kFVbQ4B_.js";import"./index-DjsccCAJ.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const r="colorVertexShader",o=`attribute position: vec3f;
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
}`;e.ShadersStoreWGSL[r]||(e.ShadersStoreWGSL[r]=o);const p=[t,n,s,l,S,a,c,d,f,m,x];for(const i of p)e.IncludesShadersStoreWGSL[i.name]||(e.IncludesShadersStoreWGSL[i.name]=i.shader);const N={name:r,shader:o};export{N as colorVertexShaderWGSL};
