#include <stdio.h>
#include <string.h>
#include <vpx/vp8cx.h>
#include <vpx/vp8dx.h>
#include <vpx/vpx_encoder.h>
#include <vpx/vpx_decoder.h>
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"Failed at line %d: %s\n",__LINE__,#x); return 1; } } while(0)
static int roundtrip(vpx_codec_iface_t *encoder, vpx_codec_iface_t *decoder) {
    vpx_codec_enc_cfg_t config;
    vpx_codec_ctx_t enc = {0}, dec = {0};
    CHECK(vpx_codec_enc_config_default(encoder, &config, 0) == VPX_CODEC_OK);
    config.g_w = 64; config.g_h = 64;
    config.g_timebase.num = 1; config.g_timebase.den = 30;
    config.g_lag_in_frames = 0; config.g_threads = 2;
    config.rc_target_bitrate = 100;
    CHECK(vpx_codec_enc_init(&enc, encoder, &config, 0) == VPX_CODEC_OK);
    CHECK(vpx_codec_dec_init(&dec, decoder, NULL, 0) == VPX_CODEC_OK);
    vpx_image_t image;
    CHECK(vpx_img_alloc(&image, VPX_IMG_FMT_I420,64,64,1));
    for (int plane=0; plane<3; plane++) {
        int size = plane ? 32 : 64;
        for (int row=0; row<size; row++)
            memset(image.planes[plane]+row*image.stride[plane],plane ? 128 : 80,size);
    }
    CHECK(vpx_codec_encode(&enc,&image,0,1,VPX_EFLAG_FORCE_KF,VPX_DL_REALTIME) == VPX_CODEC_OK);
    vpx_codec_iter_t packets = NULL;
    const vpx_codec_cx_pkt_t *packet;
    int frames = 0;
    while ((packet = vpx_codec_get_cx_data(&enc,&packets))) {
        if (packet->kind != VPX_CODEC_CX_FRAME_PKT) continue;
        CHECK(vpx_codec_decode(&dec,packet->data.frame.buf,(unsigned int)packet->data.frame.sz,NULL,0) == VPX_CODEC_OK);
        vpx_codec_iter_t images = NULL;
        vpx_image_t *decoded;
        while ((decoded = vpx_codec_get_frame(&dec,&images))) {
            CHECK(decoded->d_w == 64 && decoded->d_h == 64);
            CHECK(decoded->planes[0][0] >= 70 && decoded->planes[0][0] <= 90);
            frames++;
        }
    }
    CHECK(frames == 1);
    vpx_img_free(&image);
    CHECK(vpx_codec_destroy(&enc) == VPX_CODEC_OK);
    CHECK(vpx_codec_destroy(&dec) == VPX_CODEC_OK);
    return 0;
}
int main(void) {
    CHECK(roundtrip(vpx_codec_vp8_cx(),vpx_codec_vp8_dx()) == 0);
    CHECK(roundtrip(vpx_codec_vp9_cx(),vpx_codec_vp9_dx()) == 0);
    puts(vpx_codec_version_str());
    puts("VP8 and VP9 encode/decode round trips passed");
    return 0;
}
