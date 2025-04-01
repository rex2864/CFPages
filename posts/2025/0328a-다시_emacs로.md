## 다시 emacs로

한동안 vscode를 주력 code editor로 사용하였었다. 좋은 tool이지만 아쉬움이 없지는 않았다.
ssh를 통한 원격 서버에 연결하여 편집을 할때 vscode는 원격 서버에 code server를 설치하게 된다.
또한, extension들도 원격 서버에 설치를 해야 사용을 할 수가 있었다.
설정도 원격 서버에 별도로 설정해야만 할 때가 있다.
로컬과 별도의 원격 서버 자체의 환경을 구축할 수 있다는 장점이 있지만...

나는 원격지에 뭔가를 설치를 해야한다는 것이 싫었다.
또한 vscode를 사용하다 보면 마우스와 방향키를 사용해야만 하는 상황들이 자주 생긴다.
이것이 별거 아닌 것처럼 생각될 수도 있지만, 오른손을 자주 옮겨 다녀야 하는 것이 불편하였다.

이러던 중에 youtube에서 emacs configuration 관련 동영상들을 보게 되었고
emacs configuration을 차근차근 다시 설정하면서 emacs로 돌아오게 되었다.

몇 주간의 study, try를 거쳐서 나름 깔끔하고 효율적인 활용성이 되도록 설정을 마무리 할 수 있었다.

```emacs-lisp
;; filename: init.el
;; location this file in "~/.config/emacs/"
;; if windows, located to "~/.emacs.d/"
;; or make symlink "~/.emacs.d/" to "~/.config/emacs/"
;; mklink /d C:\Users\userid\AppData\Roaming\.emacs.d C:\Users\userid\AppData\Roaming\.config\emacs

;; add melpa and elpa repository
(require 'package)
(add-to-list 'package-archives '("melpa" . "https://melpa.org/packages/"))
(package-initialize)
(unless package-archive-contents (package-refresh-contents))
(unless (package-installed-p 'use-package) (package-install 'use-package))
(require 'use-package)
(setq use-package-always-ensure t)

;; set extra lisp script loading path
;; (add-to-list 'load-path "~/.config/emacs/scripts/")

;; maximize frame. in tiling window manager, not needed
;; (set-frame-parameter (selected-frame) 'fullscreen 'maximized)
;; (add-to-list 'default-frame-alist '(fullscreen . maximized))

;; startup buffer disable
(setq inhibit-startup-screen 1)
;; do not make backup file
(setq backup-inhibited 1)
;; instead no backup file, all backup file create in TRASH directory
;; (setq backup-directory-alist '((".*" . "~/.Trash")))
;; disable bell sound instead display it
(setq visible-bell 1)

;; encoding
(prefer-coding-system 'utf-8-unix)
(set-terminal-coding-system 'utf-8-unix)
(set-keyboard-coding-system 'utf-8-unix)

;; global indent setting: use space
(setq-default indent-tabs-mode nil)
;; global tab width set to 4 (combined above, 4 space)
(setq-default tab-width 4)
;; for c/c++ language, indent offset set to 4 width
(setq-default c-basic-offset 4)
;; coding style setting for C/C++ language
(setq c-default-style "stroustrup")
;; insert braces start, end insert automatically
(electric-pair-mode 1)

;; emacs UI components
(menu-bar-mode -1)
(scroll-bar-mode -1)
(tool-bar-mode -1)
(tooltip-mode -1)

;; theme
(load-theme 'wombat)

;; line/column numbers and line wrapping
(column-number-mode 1)
(global-display-line-numbers-mode 1)
(global-visual-line-mode 1)
(dolist (mode '(term-mode-hook
                shell-mode-hook
                eshell-mode-hook))
  (add-hook mode (lambda () (display-line-numbers-mode 0))))

;; fonts
(set-face-attribute 'default nil
                    :font "D2Coding"
                    :height 140
                    :weight 'medium)
(set-face-attribute 'variable-pitch nil
                    :font "NanumGothic"
                    :height 140
                    :weight 'medium)
(set-face-attribute 'fixed-pitch nil
                    :font "D2Coding"
                    :height 140
                    :weight 'medium)
;; for hangul font
(set-fontset-font t 'hangul (font-spec :name "D2Coding"))

;; minibuffer escape
(global-set-key [escape] 'keyboard-escape-quit)

;; zoom in/out keybindings
(global-set-key (kbd "C-=") 'text-scale-increase)
(global-set-key (kbd "C--") 'text-scale-decrease)

;; mark set keybindings with Ctrl-Space
(global-set-key [C-kanji] 'set-mark-command)

;; move focus between buffers with meta-<arrow> keybindings
(windmove-default-keybindings 'meta)
(global-set-key (kbd "M-k") 'windmove-up)
(global-set-key (kbd "M-j") 'windmove-down)
(global-set-key (kbd "M-h") 'windmove-left)
(global-set-key (kbd "M-l") 'windmove-right)

;; beacon
(use-package beacon)
(beacon-mode 1)

;; buffer move (need to install buffer-move package first)
(use-package buffer-move)
(global-set-key (kbd "C-M-<up>")    'buf-move-up)
(global-set-key (kbd "C-M-<down>")  'buf-move-down)
(global-set-key (kbd "C-M-<left>")  'buf-move-left)
(global-set-key (kbd "C-M-<right>") 'buf-move-right)
(global-set-key (kbd "C-M-k")       'buf-move-up)
(global-set-key (kbd "C-M-j")       'buf-move-down)
(global-set-key (kbd "C-M-h")       'buf-move-left)
(global-set-key (kbd "C-M-l")       'buf-move-right)

;; clang-format (clang-format command line tool needed)
(use-package clang-format)
(global-set-key (kbd "C-c i") 'clang-format-region)
(global-set-key (kbd "C-c u") 'clang-format-buffer)
(setq clang-format-style-option "microsoft")

;; diminish, company and company-box for completion
(use-package diminish)
(use-package company
  :defer 2
  :diminish
  :custom
  (company-begin-commands '(self-insert-command))
  (company-idle-delay .1)
  (company-minimum-prefix-length 2)
  (company-show-numbers t)
  (company-tooltip-align-annotations 't)
  (global-company-mode t))
(use-package company-box
  :after company
  :diminish
  :hook (company-mode . company-box-mode))

;; dired
(setq dired-kill-when-opening-new-dired-buffer t)
(setq dired-listing-switches "-AhlX --group-directories-first")

;; markdown-mode
(use-package markdown-mode)

;; reload initialize config file
(defun reload-init-file ()
  (interactive)
  (load-file user-init-file)
  (load-file user-init-file))

(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(markdown-code-face ((t nil))))
```

emacs를 실행할때 locale 설정이 맞지 않으면 한글 입력이 되지 않는다.

~/../usr/share/applications/emacs.desktop 파일에서 emacs 실행 명령에 locale 설정을 추가한다.

```bash
Exec=env LC_CTYPE=ko_KR.UTF-8 emacs %F
```

---

Date: 2025. 03. 28

Tags: emacs
