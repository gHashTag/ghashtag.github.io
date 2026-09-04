import{S as e}from"./QueenCombBabylon-C8Ncj2QC.js";import{b as t,a as n,i as a,c,d}from"./bakedVertexAnimation-BgI3xQxY.js";import{c as s,a as f}from"./clipPlaneVertex-CPFEvATq.js";import{f as l}from"./fogVertexDeclaration-DGNZOUzk.js";import{i as S}from"./instancesDeclaration-Drr-9F79.js";import{f as m}from"./fogVertex-Bw3VG-dM.js";import{v as x}from"./vertexColorMixing-fG9KUQxe.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-whyUdQOo.js";import"./index-BtJgdu3X.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const r="colorVertexShader",o=`attribute position: vec3f;
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
