import{S as o}from"./QueenCombBabylon-Ccpv0aSp.js";import"./react-Be6y7_DR.js";import"./three-C7rSOEFP.js";import"./Queen-kFVbQ4B_.js";import"./index-DjsccCAJ.js";import"./motion-CsGAkEsf.js";import"./router-BHJoP3Ih.js";const r="shadowMapFragmentSoftTransparentShadow",a=`#if SM_SOFTTRANSPARENTSHADOW==1
if ((bayerDither8(floor(mod(gl_FragCoord.xy,8.0))))/64.0>=softTransparentShadowSM.x*alpha) discard;
#endif
`;o.IncludesShadersStore[r]||(o.IncludesShadersStore[r]=a);const i={name:r,shader:a};export{i as shadowMapFragmentSoftTransparentShadow};
