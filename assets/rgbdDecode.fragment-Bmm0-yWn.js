import{ar as e}from"./ray-nqp9MIGV.js";import{h as i}from"./helperFunctions-B9Y7H3oJ.js";import"./react-BikoVsHo.js";import"./QueenUniverse-ySrqazwA.js";import"./index-BZfTeQdo.js";import"./motion-DmZWFm6O.js";import"./router-CAi4bOxy.js";import"./specCatalog-ONQ2RJG4.js";const o="rgbdDecodePixelShader",t=`varying vec2 vUV;uniform sampler2D textureSampler;
#include<helperFunctions>
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=vec4(fromRGBD(texture2D(textureSampler,vUV)),1.0);}`;e.ShadersStore[o]||(e.ShadersStore[o]=t);const a=[i];for(const r of a)e.IncludesShadersStore[r.name]||(e.IncludesShadersStore[r.name]=r.shader);const h={name:o,shader:t};export{h as rgbdDecodePixelShader};
