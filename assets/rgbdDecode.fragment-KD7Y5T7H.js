import{ar as e}from"./QueenComb-DWw-ZfuD.js";import{h as i}from"./helperFunctions-DC6vk6zf.js";import"./index-D4ZaLqj7.js";import"./react-BikoVsHo.js";import"./motion-DmZWFm6O.js";import"./router-CAi4bOxy.js";import"./queenRepositoryWorld-DQIYnztg.js";const o="rgbdDecodePixelShader",t=`varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=vec4(fromRGBD(texture2D(textureSampler,vUV)),1.0);}`;e.ShadersStore[o]||(e.ShadersStore[o]=t);const a=[i];for(const r of a)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const p={name:o,shader:t};export{p as rgbdDecodePixelShader};
