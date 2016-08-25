/*
** getinfo.c for  in /home/eax/dev/nfc_ex/tisseo
** 
** Made by eax
** Login   <soules_k@epitech.net>
** 
** Started on  Sat Jun  7 00:02:55 2014 eax
** Last update Thu Aug 25 02:15:03 2016 eax
*/

#include <stdlib.h>
#include <nfc/nfc.h>

#define MAX_FRAME_LEN 300

#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

void    nfcerror_exit(nfc_device *pnd, char *s)
{
  nfc_perror(pnd, s);
  exit(EXIT_FAILURE);
}

void show(size_t recvlg, uint8_t *recv)
{
  size_t i;

  printf("< ");
  for(i = 0 ; i < recvlg ; i++) {
    printf("%02x ",(unsigned int) recv[i]);
  }
  printf("\n");
}


void print_nfc_target(const nfc_target *pnt, bool verbose)
{
  char *s;
  str_nfc_target(&s, pnt, verbose);
  printf("%s", s);
  nfc_free(s);
}

int	main(int ac, char **av)
{
  int		ret;
  nfc_context   *ctx;
  nfc_device    *pnd;
  nfc_target	nt;
  int	fd;

  const nfc_modulation nm = { .nmt = NMT_ISO14443A, .nbr = NBR_106 };
  memset(&nt, 0, sizeof(nt));

  if (ac != 2)
    {
      printf("Usage: %s output_file\n", *av);
      return (0);
    }

  nfc_init(&ctx);
  pnd = nfc_open(ctx, NULL);
  if (!pnd)
    {
      fprintf(stderr, "Unable to connect to NFC device.\n");
      exit(EXIT_FAILURE);
    }

  if (nfc_initiator_init(pnd) < 0)
    nfcerror_exit(pnd, "nfc_initiator_init()");

  printf("NFC reader: %s opened\n", nfc_device_get_name(pnd));


  if ((ret = nfc_initiator_select_passive_target(pnd, nm, NULL, 0, &nt)) <= 0)
    nfcerror_exit(pnd, "nfc_initiator_poll_target()");

  print_nfc_target(&nt, 1);

  fd = open(av[1], O_RDWR | O_CREAT,  S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);
  if (fd < 0)
    {
      printf("open(): %m\n");
      exit(EXIT_FAILURE);
    }

  write(fd, &nt, sizeof(nt));
  close(fd);

  nfc_close(pnd);
  nfc_exit(ctx);

  return (0);
}
