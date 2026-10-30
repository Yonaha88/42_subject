/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   codexion.h                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/10/06 12:23:40 by kyonaha           #+#    #+#             */
/*   Updated: 2026/10/23 21:28:05 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CODEXION_H
# define CODEXION_H

# include <stdio.h>
# include <string.h>
# include <stdlib.h>
# include <limits.h>
# include <unistd.h>
# include <pthread.h>
# include <sys/time.h>

# define MONITOR_INTERVAL_US 1000
# define SLEEP_STEP_US 5000
# define WAIT_CAP_US 50000
# define PRECISE_WINDOW_US 8000
# define QUEUE_MAX 2

typedef enum e_scheduler
{
	CODEX_FIFO,
	CODEX_EDF
}	t_scheduler;

typedef struct s_args
{
	int			number_of_coders;
	long		time_to_burnout;
	long		time_to_compile;
	long		time_to_debug;
	long		time_to_refactor;
	int			number_of_compiles_required;
	long		dongle_cooldown;
	t_scheduler	scheduler;
}	t_args;

typedef struct s_request
{
	long	key;
	long	ticket;
	int		coder_id;
}	t_request;

typedef struct s_heap
{
	t_request	items[QUEUE_MAX];
	int			size;
}	t_heap;

typedef struct s_dongle
{
	pthread_mutex_t	mutex;
	int				holder;
	long			available_at;
	t_heap			queue;
}	t_dongle;

typedef struct s_coder
{
	int				id;
	t_dongle		*first;
	t_dongle		*second;
	long			last_compile;
	int				compiles;
	pthread_mutex_t	state_mutex;
	pthread_cond_t	wake;
	pthread_t		thread;
	struct s_table	*table;
}	t_coder;

typedef struct s_table
{
	t_args			args;
	t_coder			*coders;
	t_dongle		*dongles;
	long			start;
	int				stop;
	long			next_ticket;
	int				arrived;
	int				started;
	pthread_mutex_t	stop_mutex;
	pthread_mutex_t	log_mutex;
	pthread_mutex_t	arbiter;
	pthread_cond_t	ready;
	pthread_t		monitor;
	int				ready_base;
	int				ready_dongles;
	int				ready_coders;
}	t_table;

int			parse_args(int argc, char **argv, t_args *args);

int			init_table(t_table *t);
void		destroy_table(t_table *t);

long		now_us(void);
void		sleep_until(t_table *t, long target);
int			is_stopped(t_table *t);
void		set_stop(t_table *t);
void		wake_all(t_table *t);

void		log_state(t_coder *c, const char *msg);
int			log_burnout(t_coder *c);
long		log_compile(t_coder *c);

int			heap_push(t_heap *h, t_request req);
t_request	*heap_peek(t_heap *h);
void		heap_pop(t_heap *h);
void		sift_up(t_heap *h, int i);
void		sift_down(t_heap *h, int i);

int			dongle_usable(t_dongle *d, long now);
long		dongle_available_at(t_dongle *d);
void		dongle_take(t_dongle *d, int id);
void		dongle_release(t_dongle *d, long available_at);

void		dongle_enqueue(t_dongle *d, t_request req);
int			dongle_is_first(t_dongle *d, int id);

void		request_dongles(t_coder *c);
int			try_take(t_coder *c);
int			take_dongles(t_coder *c);
void		release_dongles(t_coder *c);

void		*coder_routine(void *arg);
void		*monitor_routine(void *arg);
void		stop_simulation(t_table *t);

#endif
