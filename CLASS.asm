.data
arrayD DWORD 1,2,3

.code
main PROC
    mov eax, arrayD        ; eax = 1
    mov ebx, arrayD+4      ; ebx = 2
    mov ecx, arrayD+8      ; ecx = 3

    mov arrayD, ecx        ; array[0] = 3
    mov arrayD+4, eax      ; array[1] = 1
    mov arrayD+8, ebx      ; array[2] = 2

    mov eax, 0
    ret
main ENDP
END main



;initial array
;load array into registers
;print back array in order