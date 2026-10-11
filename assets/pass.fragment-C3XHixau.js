import{a$ as e}from"./QueenComb-DXeI76YC.js";import"./index-FdDJ0gLe.js";import"./react--6nd5XBq.js";import"./motion-CvAcPNoJ.js";import"./router-CmS70aoX.js";const r="passPixelShader",o=`varying vec2 vUV;uniform sampler2D textureSampler;
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void) 
{gl_FragColor=texture2D(textureSampler,vUV);}`;e.ShadersStore[r]||(e.ShadersStore[r]=o);const S={name:r,shader:o};export{S as passPixelShader};
