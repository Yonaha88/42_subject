/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   get_next_line.h                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/09 11:26:51 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/12 18:26:41 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef GET_NEXT_LINE_H
# define GET_NEXT_LINE_H

# include <stdlib.h>
# include <unistd.h>

# ifndef OPEN_MAX
#  define OPEN_MAX 1024
# endif

# ifndef BUFFER_SIZE
#  define BUFFER_SIZE 42
# endif

void	*ft_memcpy(void *dest, const void *src, size_t num);
size_t	ft_strlen(const char *s);
char	*append(char *dest, char *src, size_t n);
int		find_nl(const char *s);
char	*get_next_line(int fd);

#endif
