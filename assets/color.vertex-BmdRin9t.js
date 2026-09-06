import{bS as e}from"./Queen-C_U0yXV5.js";import{b as t,a as o,i as a,c,d,e as s}from"./bakedVertexAnimation-CoI7ufvn.js";import{c as f,a as l}from"./clipPlaneVertex-CKp8suqU.js";import{f as S}from"./fogVertexDeclaration-QyOZnKhP.js";import{f as m}from"./fogVertex-BkQ_w04A.js";import{v as x}from"./vertexColorMixing-DpTFwPyI.js";import"./index-R51P2USl.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const r="colorVertexShader",n=`attribute position: vec3f;
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
}`;e.ShadersStoreWGSL[r]||(e.ShadersStoreWGSL[r]=n);const u=[t,o,f,S,a,c,d,s,l,m,x];for(const i of u)e.IncludesShadersStoreWGSL[i.name]||(e.IncludesShadersStoreWGSL[i.name]=i.shader);const C={name:r,shader:n};export{C as colorVertexShaderWGSL};
