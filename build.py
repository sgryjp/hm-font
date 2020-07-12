import logging
from pathlib import Path

import fontforge as ff
import psMat

__version__ = "20.7.5"
__copyright__ = "Copyright (c) 2020, Suguru Yamamoto"
_logger = logging.getLogger(__name__)


if __name__ == "__main__":
    import os
    import sys
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-i", "--input", required=True, type=Path,
                        help="path to read source font file")
    parser.add_argument("-o", "--output", required=True, type=Path,
                        help="path to write the composed font file")
    args = parser.parse_args()

    # ロガーを設定
    logging.basicConfig(format="[%(asctime)s] %(message)s",
                        level=logging.DEBUG)

    # フォントをロード
    hack: ff.font = ff.open(str(args.input / "Hack-Regular.ttf"))
    mplus: ff.font = ff.open(str(args.input / "mplus-1m-regular.ttf"))

    # フォントのサイズ調整用に「M」の字でサイズ比と差を計算。
    # ただし Hack と M+1M は文字の縦横比が違うため、単純な拡縮ではマッチしない。
    # ここでは、まず高さを一致させ、横幅の拡大率を高さの 1.1 倍を超えない程度に
    # 抑え、かつ不足する横幅を記録しておく（これを元にパディング量を調整し、
    # いわゆる全角文字の幅が英数字のちょうど 2 倍になるようにする）
    vert_ratio = hack[0x4d].vwidth / mplus[0x4d].vwidth
    horiz_ratio = min(hack[0x4d].width / mplus[0x4d].width, vert_ratio * 1.1)
    horiz_pad = int(hack[0x4d].width - mplus[0x4d].width * horiz_ratio)
    scaling_ratio = psMat.scale(horiz_ratio, vert_ratio)
    _logger.info("scaling ratio: %s", scaling_ratio)
    _logger.info("horizontal padding: %s", horiz_pad)

    # Hack に無く M+ にあるコードポイントを列挙する
    font_code_points = set(g.encoding for g in hack.glyphs())
    mplus_code_points = set(g.encoding for g in mplus.glyphs())
    for code_point in mplus_code_points - font_code_points:
        # BMP の外にある文字は無視する
        if 0xffff < code_point:
            continue

        try:
            # この M+ のグリフを Hack に合うよう拡縮とパディング挿入を行う
            g = mplus[code_point]
            g.transform(scaling_ratio)
            g.left_side_bearing = int(g.left_side_bearing + horiz_pad / 2)
            g.right_side_bearing = int(g.right_side_bearing + horiz_pad / 2)
            g.width = int(g.width + horiz_pad)

            # このグリフを Hack の方にコピー
            mplus.selection.select(code_point)
            mplus.copy()
            hack.selection.select(code_point)
            hack.paste()
        except Exception as e:
            _logger.warning("Error on copying %s (%s): %s",
                            mplus[code_point], f"u{code_point:x}", e)

    # フォントのメタ情報を生成
    try:
        hack_version = hack.sfnt_names[5][2].split(";")[0].lower()
    except Exception as e:
        _logger.error("Failed to extrace Hack version: %s\n\n%s",
                      e, hack.sfnt_names)
        sys.exit(2)
    try:
        mplus_version = mplus.sfnt_names[5][2].lower()
    except Exception as e:
        _logger.error("Failed to extrace M+ version: %s\n\n%s",
                      e, mplus.sfnt_names)
        sys.exit(2)
    version_string = ("Version {}; derivative of Hack {} and M+1m {}"
                      .format(__version__, hack_version, mplus_version))
    license_text = Path("LICENSE").read_text()

    # フォントに設定
    family_name = "HM"
    subfamily_name = "Regular"
    hack.fontname = f"{family_name}-{subfamily_name}"
    hack.familyname = family_name
    hack.fullname = f"{family_name} {subfamily_name}"
    locale = "English (US)"
    license_url = "https://github.com/sgryjp/hm-font/blob/master/LICENSE"
    meta = (
        __copyright__,  # 0:Copyright
        family_name,  # 1:Family
        subfamily_name,  # 2:SubFamily
        f"{family_name}-{subfamily_name}-{__version__}",  # 3:UniqueID
        hack.fullname,  # 4:Fullname
        version_string,  # 5:Version
        f"{family_name}-{subfamily_name}",  # 6:PostScriptName
        "",  # 7:Trademark
        "",  # 8:Manufacturer
        "",  # 9:Designer
        "",  # 10:Descriptor
        "",  # 11:Vendor URL
        "",  # 12:Designer URL
        license_text,  # 13:License
        license_url,  # 14:License URL
        None,  # 15:N/A
        family_name,  # 16:Preferred Family
        subfamily_name,  # 17:Preferred Styles
    )
    for i, value in enumerate(meta):
        if value is not None:
            hack.appendSFNTName(locale, i, value)

    # デバッグ用に設定したメタ情報を表示
    for _, k, v in hack.sfnt_names:
        if k != "License":
            _logger.debug("[%s]", k)
            _logger.debug("%s", v)

    # フォントを出力
    os.makedirs(args.output, exist_ok=True)
    hack.generate(str(args.output / "hm-regular.ttf"))
