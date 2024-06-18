import os
import random
import sys
import pygame as pg
import math


WIDTH, HEIGHT = 1600, 900
KEY = {pg.K_UP:(0, -5),
       pg.K_DOWN:(0, +5),
       pg.K_LEFT:(-5, 0),
       pg.K_RIGHT:(+5, 0),}
f = True
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def fly_direction(kk_img: pg.Surface) -> dict[tuple[int, int]:pg.Surface]:
    """
    1.飛ぶ方向に従ってこうかとん画像を切り替える
    引数：こうかとん画像のSurface
    戻り値：辞書
    {押下キーに対する移動量の合計値タプル:rotozoomしたSurface}
    """
    fly_kk = {(-5, 0):pg.transform.rotozoom(kk_img, 0, 1.0),
              (-5, +5):pg.transform.rotozoom(kk_img, 45, 1.0),
              (-5, -5):pg.transform.rotozoom(kk_img, -45, 1.0),
              (0, +5):pg.transform.rotozoom(pg.transform.flip(kk_img, True, False), -90, 1.0),
              (+5, +5):pg.transform.rotozoom(pg.transform.flip(kk_img, True, False), -45, 1.0),
              (+5, 0):pg.transform.rotozoom(pg.transform.flip(kk_img, True, False), 0, 1.0),
              (+5, -5):pg.transform.rotozoom(pg.transform.flip(kk_img, True, False), 45, 1.0),
              (0, -5):pg.transform.rotozoom(pg.transform.flip(kk_img, True, False), 90, 1.0)}
    return fly_kk


def bom_setting() -> tuple[list, list]:
    """
    2.時間とともに爆弾が拡大, 加速する
    引数：なし
    戻り値：タプル(加速度のリスト, 拡大爆弾Surfaceのリスト)
    """
    bb_list = []
    saccs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_list.append(bb_img)
    return saccs, bb_list


def game_over(screen: pg.Surface) -> None:
    """
    3.ゲームオーバー画面
    引数：Surface
    戻り値：なし
    """
    go_img = pg.Surface((WIDTH, HEIGHT))  #画面サイズと同じSurfaceを用意する
    pg.draw.rect(go_img, (0, 0, 0), (0, 0, WIDTH, HEIGHT))  #画面サイズと同じ黒い四角を描画する
    go_img.set_alpha(128)  #四角を半透明にする
    screen.blit(go_img, [0, 0])  #半透明の四角をScreenに貼り付ける
    fonto = pg.font.Font(None, 80)  #文字の大きさを80にする
    txt = fonto.render("Game Over", True, (255, 255, 255))  #白文字でGame Overと書いたSurfaceをtxtに入れる
    screen.blit(txt, [WIDTH/2-152, HEIGHT/2-10])  #画面中央にGame Overと表示する
    cry_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 2.0)  #泣いているこうかとん画像を2倍に拡大する
    screen.blit(cry_kk_img, [WIDTH/2-260, HEIGHT/2-60])  #文字の左側に泣いているこうかとんを表示
    screen.blit(cry_kk_img, [WIDTH/2+170, HEIGHT/2-60])  #文字の右側に泣いているこうかとんを表示
    t = 0
    clock = pg.time.Clock()
    while t <= 5:  #5秒になるまで
        pg.display.update()
        clock.tick(1)
        t += 1


def follow_bom(bb_pos: tuple[int, int], kk_pos: tuple[int, int]) -> tuple[int, int]:
    """
    4.追従型爆弾
    引数：爆弾の現在座標(x, y), こうかとんの現在座標(x, y)
    戻り値：タプル(爆弾の速度x成分, 爆弾の速度y成分)
    """
    global f
    dx = bb_pos[0] - kk_pos[0]
    dy = bb_pos[1] - kk_pos[1]
    print(dx^2, dy^2)
    d = abs(dx^2+dy^2)
    if d < 300 and f:
        dx, dy = -5, 0
    else:
        f = False
        dx /= d
        dy /= d
        dx *= math.sqrt(50)
        dy *= math.sqrt(50)
        print(dx, dy)
    return dx, dy


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：タプル(横方向判定結果, 縦方向判定結果)
    画面外ならTrue, 画面外ならFalse
    """
    yoko, tate = True, True
    if obj_rct.left <= 0 or WIDTH <= obj_rct.right: #横方向判定
        yoko = False
    if obj_rct.top <= 0 or HEIGHT <= obj_rct.bottom: #縦方向判定
        tate = False
    return yoko, tate


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 2.0)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 900, 400

    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = +5, +5

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            game_over(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for k, v in KEY.items():
            if key_lst[k]:
                sum_mv[0] += v[0]
                sum_mv[1] += v[1]
        kk_rct.move_ip(sum_mv)
        if (not check_bound(kk_rct)[0]) or (not check_bound(kk_rct)[1]):  #こうかとん衝突判定
            kk_rct.move_ip((sum_mv[0]*-1, sum_mv[1]*-1))
        try:
            screen.blit(fly_direction(kk_img)[tuple(sum_mv)], kk_rct)  #押下キーが矢印キーだった場合
        except KeyError:
            screen.blit(kk_img, kk_rct)  #何も押してない or 押下キーが矢印キー以外だった場合
        
        #print((kk_rct[0], kk_rct[1]), (bb_rct[0], bb_rct[1]))
        #vx = follow_bom((kk_rct[0], kk_rct[1]), (bb_rct[0], bb_rct[1]))[0]
        #vy = follow_bom((kk_rct[0], kk_rct[1]), (bb_rct[0], bb_rct[1]))[1]
        bb_accs = bom_setting()[0]  #爆弾の加速度のリストを入れる
        bb_imgs = bom_setting()[1]  #拡大爆弾のSurfaceのリストを入れる
        avx = vx*bb_accs[min(tmr//500, 9)]  #加速度x方向を掛けたavxを作成
        avy = vy*bb_accs[min(tmr//500, 9)]  #加速度y方向を掛けたavyを作成
        bb_img = bb_imgs[min(tmr//500, 9)]  #拡大された爆弾をbb_imgに入れる
        bb_img.set_colorkey((0, 0, 0))  #爆弾の周りを透明にする
        bb_rct.move_ip((avx, avy))  #爆弾を動かす
        if not check_bound(bb_rct)[0]:  #爆弾が左右の壁に衝突したら
            vx *= -1  #x成分を反転させる
        if not check_bound(bb_rct)[1]:  #爆弾が上下の壁に衝突したら
            vy *= -1  #y成分を反転させる
        screen.blit(bb_img, bb_rct)  #爆弾SurfaceをScreenに貼り付ける
        pg.display.update()  #画面を更新する
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
