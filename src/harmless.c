#include <stdio.h>
#include <string.h>

#include "base.h"
#include "position.h"
#include "search.h"
#include "ucci.h"

FILE *logfile;

int main(int argc, char *argv[])
{
    ucci_comm_enum uce;
    ucci_comm_struct ucs;
    char bookfile[255] = "book.data";

#ifdef DEBUG_LOG
    logfile = fopen("harmless.log", "w");
#endif

    setvbuf(stdin, NULL, _IOLBF, 0);
    setvbuf(stdout, NULL, _IOLBF, 0);

    if (boot_line() == UCCI_COMM_UCCI) {
        new_hash_table();
        init_openbook(bookfile);

        printf("id name harmless\n");
        printf("id copyright 2011\n");
        printf("id anthor timebug\n");
        printf("ucciok\n");

        uce = UCCI_COMM_NONE;

        while (uce != UCCI_COMM_QUIT) {
            uce = idle_line(&ucs);

            switch (uce) {
            case UCCI_COMM_ISREADY:
                printf("readyok\n");
                fflush(stdout);
                break;
            case UCCI_COMM_STOP:
                printf("nobestmove\n");
                fflush(stdout);
                break;
            case UCCI_COMM_POSITION:
                fen_to_arr(ucs.position.fen_str);
                fflush(stdout);
                break;
            case UCCI_COMM_BANMOVES:
                break;
            case UCCI_COMM_SETOPTION:
                switch (ucs.option.uo_type) {
                case UCCI_OPTION_BATCH:
                    break;
                case UCCI_OPTION_DEBUG:
                    break;
                case UCCI_OPTION_NEWGAME:
                    new_hash_table();
                    init_openbook(bookfile);
                    break;
                default:
                    break;
                }

                break;
            case UCCI_COMM_GO:
            case UCCI_COMM_GOPONDER:
                if(ucs.search.ut_mode == UCCI_TIME_DEPTH)
                    think(ucs.search.depth_time.depth);
                break;
            default:
                break;
            }
        }

        del_hash_table();
    }

#ifdef DEBUG_LOG
    fclose(logfile);
#endif

    printf("bye\n");

    return 0;
}
