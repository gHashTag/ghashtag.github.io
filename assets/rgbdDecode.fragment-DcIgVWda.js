import{bI as e}from"./Queen-Cw0Rpa4M.js";import{h as i}from"./helperFunctions-B5ZvZ9Ab.js";import"./index-DRQo-Ljl.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-DHWxIZD9.js";const o="rgbdDecodePixelShader",t=`varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=vec4(fromRGBD(texture2D(textureSampler,vUV)),1.0);}`;e.ShadersStore[o]||(e.ShadersStore[o]=t);const n=[i];for(const r of n)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const l={name:o,shader:t};export{l as rgbdDecodePixelShader};
