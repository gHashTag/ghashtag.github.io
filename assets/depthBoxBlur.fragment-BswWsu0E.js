import{S as r}from"./QueenCombBabylon-CfZ2XGau.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-BpVVE5sQ.js";import"./index-CEfZVCAR.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const e="depthBoxBlurPixelShader",o=`varying vec2 vUV;uniform sampler2D textureSampler;uniform vec2 screenSize;
#define CUSTOM_FRAGMENT_DEFINITIONS
void main(void)
{vec4 colorDepth=vec4(0.0);for (int x=-OFFSET; x<=OFFSET; x++)
for (int y=-OFFSET; y<=OFFSET; y++)
colorDepth+=texture2D(textureSampler,vUV+vec2(x,y)/screenSize);gl_FragColor=(colorDepth/float((OFFSET*2+1)*(OFFSET*2+1)));}`;r.ShadersStore[e]||(r.ShadersStore[e]=o);const c={name:e,shader:o};export{c as depthBoxBlurPixelShader};
