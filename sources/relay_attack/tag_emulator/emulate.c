#include <stdlib.h>
#include <nfc/nfc.h>
#include <err.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>

#define MAX_FRAME_LEN 300
#define SAK_ISO14443_4_COMPLIANT 0x20


void    nfcerror_exit(nfc_device *pnd, char *s)
{
  nfc_perror(pnd, s);
  exit(EXIT_FAILURE);
}

void show(size_t recvlg, uint8_t *recv, char *prompt)
{
  size_t i;

  printf("%s ", prompt);
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
  uint8_t       bufRx[MAX_FRAME_LEN] = {};

  int		ret;
  int		fd;
  nfc_context   *ctx;
  nfc_device    *pnd;

  nfc_target nt = {
    .nm = {
      .nmt = NMT_ISO14443A,
      .nbr = NBR_UNDEFINED,
    },
    .nti = {
      .nai = {
        .abtAtqa = { 0x00, 0x04 },
        .abtUid = { 0x08, 0xab, 0xcd, 0xef },
        .btSak = 0x09,
        .szUidLen = 4,
        .szAtsLen = 0,
      },
    },
  };


  
  if (ac != 2)
    {
      printf("Usage: %s input_file\n", *av);
      return (0);
    }

  fd = open(av[1], O_RDONLY);
  if (fd < 0)
    {
      printf("open(): %m\n");
      exit(EXIT_FAILURE);
    }
  read(fd, &nt, sizeof(nt));
  close(fd);


  
  int fifo_from_real_card;
  int fifo_to_real_card;

  if ((fifo_from_real_card = open("/tmp/from_real_card", O_RDONLY | O_NONBLOCK)) < 0)
    err(1, "open(from real card)");
  if ((fifo_to_real_card = open("/tmp/to_real_card", O_WRONLY)) < 0)
    err(1, "open(to real card)");

  
  int flags = fcntl(fifo_from_real_card, F_GETFL, 0);
  if (fcntl(fifo_from_real_card, F_SETFL, flags | O_NONBLOCK) < 0)
    err(1, "fcntl");

  
  nfc_init(&ctx);




  printf("=> %zu\n", nt.nti.nai.szUidLen);
  nt.nti.nai.szUidLen = 4;
  nt.nti.nai.abtUid[0] = 0x08;
  

  printf("We will emulate:\n");
  print_nfc_target(&nt, false);




  printf("=================== Before nfc_open ===================\n");
  fflush(stdout);
  pnd = NULL;
  printf("=================== Waiting for the reader to be connected... ===================\n");
  fflush(stdout);
  while (!pnd)
    {
      pnd = nfc_open(ctx, NULL);
      usleep(1000 * 1000);
    }
  printf("=================== After nfc_open ===================\n");
  fflush(stdout);

     
  printf("=================== Before target_init ===================\n");
  fflush(stdout);
  if ((ret = nfc_target_init(pnd, &nt, bufRx, MAX_FRAME_LEN, 0)) < 0)
    nfcerror_exit(pnd, "nfc_initiator_init()");
  printf("ret: %d\n", ret);
  show(ret, bufRx, "<");
  printf("=================== After target_init ===================\n");
  fflush(stdout);


  int have_rx = 0;
  
  while (1)
    {
      /* printf("=================== Before receive_bytes ===================\n"); */
      /* fflush(stdout); */
      ret = -6;
      if (!have_rx && (ret = nfc_target_receive_bytes(pnd, bufRx, MAX_FRAME_LEN, 1000)) < 0 && ret != -6)
  	{
  	  printf("ret: %d\n", ret);
  	  nfcerror_exit(pnd, "nfc_target_receive_bytes()");
  	}
      if (ret != -6)
	{
	  have_rx = 1;
	  show(ret, bufRx, "<");
	  /* printf("=================== After receive_bytes ===================\n"); */
	  /* fflush(stdout); */
	  write(fifo_to_real_card, bufRx, ret);
	}


      if ((ret = read(fifo_from_real_card, bufRx, MAX_FRAME_LEN)) < 0 && errno != 11)
	{
	  printf("%d\n", ret);
	  printf("%d\n", errno);
	  err(1, "read(fifo_from_real_card %d ", ret);
	}
      

      if (ret > 0)
      	{
	  have_rx = 0;
      	  /* printf("=================== Before send_bytes ===================\n"); */
      	  /* fflush(stdout); */
      	  if ((ret = nfc_target_send_bytes(pnd, bufRx, ret, 0)) < 0)
      	    {
      	      printf("ret: %d\n", ret);
      	      nfcerror_exit(pnd, "nfc_target_send_bytes()");
      	    }
	  show(ret, bufRx, ">");
      	  /* printf("=================== After send_bytes ===================\n"); */
      	  /* fflush(stdout); */
      	}

    }

  return (0);
}
